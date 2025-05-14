from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import joblib
import numpy as np

# Simulando dados de clientes
data = {
    'idade': [25, 30, 35, 40, 28, 33, 45, 50, 22, 27, 38, 29],
    'frequencia': [5, 3, 2, 1, 4, 5, 1, 1, 6, 4, 2, 3],
    'cancelou':   [0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1]  # 0 = Não cancelou, 1 = Cancelou
}

# Criando DataFrame
df = pd.DataFrame(data)

# Separando variáveis independentes (X) e dependente (y)
X = df[['idade', 'frequencia']]
y = df['cancelou']

# Dividindo os dados para treino e teste com random_state para reprodutibilidade
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinando o modelo
model = LogisticRegression()
model.fit(X_train, y_train)

# Fazendo previsões
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

# Salvando o modelo treinado
joblib.dump(model, 'modelo_cancelamento.pkl')

# Mensagem de sucesso
print("✅ Modelo treinado e salvo como 'modelo_cancelamento.pkl'.")
print(f"📊 Acurácia do modelo: {accuracy * 100:.2f}%")
