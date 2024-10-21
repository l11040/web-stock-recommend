from flask import Blueprint, jsonify
from ..services.stock_service import get_recent_stock_data
from ..services.prediction_service import save_predictions_to_db
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, Bidirectional, Conv1D, Attention, Concatenate
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import L1L2

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/run', methods=['GET'])
def run_prediction():
    # 최근 100일간의 데이터를 DB에서 불러오기
    stock_data = get_recent_stock_data(100)
    
    # 데이터프레임으로 변환 (종가 데이터만 추출)
    data = [{'date': s.date, f'close_price_{s.stock_code}': s.close_price} for s in stock_data]
    df = pd.DataFrame(data)

    # 데이터 피벗 (날짜 기준으로 종목을 열로 설정)
    df_pivot = df.pivot_table(index='date', values=[col for col in df.columns if 'close_price' in col])

    # 날짜 순으로 정렬
    df_pivot.sort_index(inplace=True)

    # 데이터 스케일링
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df_pivot.values)
    
     # 입력 데이터 생성
    def create_dataset(data, lookback):
        X, Y = [], []
        for i in range(len(data) - lookback):
            X.append(data[i:i+lookback])
            Y.append(data[i+lookback])
        return np.array(X), np.array(Y)

    lookback = 20
    X, Y = create_dataset(scaled_data, lookback)
    
    # 모델 구성
    input_layer = Input(shape=(lookback, df_pivot.shape[1]))
    conv_layer = Conv1D(64, 3, activation='relu')(input_layer)
    lstm_layer = Bidirectional(LSTM(128, return_sequences=True))(conv_layer)

    # Attention 레이어 구성
    query = Dense(128)(lstm_layer)
    key = Dense(128)(lstm_layer)
    value = Dense(128)(lstm_layer)
    attention_output = Attention()([query, value, key])
    concat_layer = Concatenate()([lstm_layer, attention_output])
    dropout_layer = Dropout(0.3)(concat_layer)
    lstm_layer2 = Bidirectional(LSTM(64))(dropout_layer)
    dropout_layer2 = Dropout(0.3)(lstm_layer2)
    output_layer = Dense(df_pivot.shape[1], kernel_regularizer=L1L2(l1=0.01, l2=0.01))(dropout_layer2)

    model = Model(inputs=input_layer, outputs=output_layer)
    model.compile(optimizer='adam', loss='mse')
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    # 모델 학습
    model.fit(X, Y, epochs=200, batch_size=4, validation_split=0.2, callbacks=[early_stopping])

    # 테스트 데이터 예측
    test_data = scaled_data[-lookback:]
    test_data = test_data.reshape(1, lookback, df_pivot.shape[1])
    y_pred = model.predict(test_data)

    # 예측 결과 역스케일링
    last_close_prices = df_pivot.iloc[-1].values.reshape(1, -1)
    y_pred = scaler.inverse_transform(y_pred)

    # 예측 가격 상승률 계산 및 저장
    price_changes = []
    for i, col in enumerate(df_pivot.columns):
        stock_code = col.split('_')[2]
        last_price = last_close_prices[0, i]
        pred_price = y_pred[0, i]
        change_percent = (pred_price - last_price) / last_price * 100
        price_changes.append((stock_code, pred_price, change_percent))

    # DB에 예측 결과 저장
    save_predictions_to_db(price_changes)

    return jsonify({"message": "Predictions have been made and saved to the database."})