import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

df = pd.read_csv("datasets/results.csv")

#para a construção das minhas listas e tabelas, vou trabalhar apenas com partidas oficiais, descartando assim os amistosos
# df = df.loc[df["tournament"] != "Friendly"]

#funções para o calculo das vitorias, derrotas e empates
def calculate_home_victories(row):
    if row["home_score"] > row["away_score"]:
        return 1
    else:
        return 0
    
def calculate_away_victories(row):
    if row["away_score"] > row["home_score"]:
        return 1
    elif (row["away_score"] < row["home_score"]):
        return 0

def calculate_home_losses(row):
    if row["home_score"] < row["away_score"]:
        return 1
    elif (row["home_score"] > row["away_score"]):
        return 0

def calculate_away_losses(row):
    if row["home_score"] > row["away_score"]:
        return 1
    elif (row["home_score"] < row["away_score"]):
        return 0  
    
def calculate_draws(row):
        if row["home_score"] == row["away_score"]:
            return 1
        else:
            return 0
        
# Aplicar as funções para calcular as vitórias, derrotas e empates dentro e fora de casa
df["home_victories"] = df.apply(calculate_home_victories, axis=1)
df["away_victories"] = df.apply(calculate_away_victories, axis=1)
df["home_losses"] = df.apply(calculate_home_losses, axis=1)
df["away_losses"] = df.apply(calculate_away_losses, axis = 1)
df["draws"] = df.apply(calculate_draws,axis=1)

# Adicionando as colunas de gols sofridos tanto fora quanto em casa
df["home_goals_conceded"] = df["away_score"]
df["away_goals_conceded"] = df["home_score"]

# Agregar os resultados por time (resultados de jogos em casa)
home_data = df.groupby("home_team").agg({"home_victories":"sum", "home_losses":"sum", "draws":"sum","home_score":"sum", "home_goals_conceded":"sum"}).reset_index()
home_data.rename(columns={"draws": "home_draws"}, inplace=True)

# Agregar os resultados por time (resultados de jogos fora de casa)
away_data = df.groupby("away_team").agg({"away_victories":"sum","away_losses":"sum","draws":"sum","away_score":"sum", "away_goals_conceded":"sum"}).reset_index()
away_data.rename(columns={"draws": "away_draws"}, inplace=True)

# juntando os dados dos jogos em casa e fora em um unico dataframe
merged_data = pd.merge(home_data, away_data, left_on="home_team", right_on="away_team", how='outer')
merged_data["team"] = merged_data["home_team"].combine_first(merged_data["away_team"])
merged_data.fillna(0, inplace=True)
merged_data.drop(columns=['away_team'], inplace=True)
merged_data.drop(columns=["home_team"], inplace=True)

#calculando os dados totais
merged_data["total_victories"] = merged_data["home_victories"] + merged_data["away_victories"]
merged_data["total_losses"] = merged_data["home_losses"] + merged_data["away_losses"]
merged_data["total_draws"] = merged_data["home_draws"] + merged_data["away_draws"]
merged_data["total_score"] = merged_data["home_score"] + merged_data["away_score"]
merged_data["total_goals_conceded"] = merged_data["home_goals_conceded"] + merged_data["away_goals_conceded"]
merged_data["total_games"] = merged_data["total_draws"] + merged_data["total_losses"] + merged_data["total_victories"]

#reorganizando as colunas do dataframe
merged_data = merged_data[["team", "total_games", "total_victories", "total_draws", "total_losses","total_score","total_goals_conceded", "home_victories", "home_draws", "home_losses",
                           "home_score","home_goals_conceded", "away_victories", "away_draws", "away_losses",
                           "away_score","away_goals_conceded"]]

#os dados já estão todos organizados para a criação de informações a partir desses dados

print("\nTop 10 seleçoes com mais jogos oficiais na história.")
print(tabulate(merged_data[["team", "total_games"]].sort_values(by="total_games", ascending=False).head(10), headers=["Seleçao","Total de jogos"], tablefmt="simple_grid", showindex="never", floatfmt=".0f"))

new_data = merged_data[merged_data["total_games"] >= 300].copy()
new_data["victory_percentage"] = (new_data["total_victories"] * 3.0 + new_data["total_draws"]) / new_data["total_games"] * 3 * 10

def format_percentage(value):
    return f"{value:.2f}%"

# Selecionar apenas as colunas desejadas e aplicar as funções de formatação
selected_data = new_data[["team", "victory_percentage", "total_victories", "total_draws", "total_losses"]].copy()
selected_data["victory_percentage"] = selected_data["victory_percentage"].apply(format_percentage)

print("\nTop 10 seleções com os melhores aproveitamentos em jogos oficiais")
print(tabulate(selected_data[["team", "victory_percentage", "total_victories", "total_draws","total_losses"]].sort_values(by="victory_percentage", ascending=False).head(10), headers=["Seleçao","Aproveitamento","Vitórias","Empates","Derrotas"], tablefmt="simple_grid", showindex="never", floatfmt=".0f"))

print("\nTop 10 seleções com os piores aproveitamentos em jogos oficiais")
print(tabulate(selected_data[["team", "victory_percentage", "total_victories", "total_draws","total_losses"]].sort_values(by="victory_percentage", ascending=True).head(10), headers=["Seleçao","Aproveitamento","Vitórias","Empates","Derrotas"], tablefmt="simple_grid", showindex="never", floatfmt=".0f"))

print("\nTop 10 seleções que mais marcaram gols em jogos oficiais")
print(tabulate(merged_data[["team", "total_score"]].sort_values(by="total_score", ascending=False).head(10), headers=["Seleçao","Gols Marcados"], tablefmt="simple_grid", showindex="never", floatfmt=".0f"))

print("\nTop 10 seleções que mais sofreram gols em jogos oficiais")
print(tabulate(merged_data[["team", "total_goals_conceded"]].sort_values(by="total_goals_conceded", ascending=False).head(10), headers=["Seleçao","Gols Sofridos"], tablefmt="simple_grid", showindex="never", floatfmt=".0f"))


golsMedia = merged_data["total_score"].sum() / df.shape[0]
homeVictoriesMedia = merged_data["home_victories"].sum() / df.shape[0]
awayVictoriesMedia = merged_data["away_victories"].sum() / df.shape[0]
drawsMedia = (merged_data["total_draws"].sum() / 2) / df.shape[0]

print(f"Media de gols por partida: {golsMedia:.2f}")
print(f"Porcentagem de vitoria dos times mandantes: {homeVictoriesMedia*100:.2f}%")
print(f"Porcentagem de vitoria dos times visitantes: {awayVictoriesMedia*100:.2f}%")
print(f"Porcentagem de empates {drawsMedia*100:.2f}%")

print(df.dtypes)

decade_bins = pd.IntervalIndex.from_tuples([(1870, 1879)] + [(i, i+9) for i in range(1880, 2020, 10)])
decade_labels = ['1870s'] + [f'{i}s' for i in range(1880, 2020, 10)]

df['date'] = pd.to_datetime(df['date'])
df["decade"] = pd.cut(df["date"].dt.year, bins=decade_bins, labels=decade_labels)

tt = df.groupby("decade").agg(
    total_home_score=("home_score", "sum"),
    total_away_score=("away_score", "sum"),
    total_partidas=("home_score", "size")
).reset_index()

plt.figure(figsize=(10, 6))

# Criar o gráfico de barras
plt.bar(tt['decade'].astype(str), tt["total_partidas"], color='red')

# Adicionar rótulos e título
plt.xlabel("Década")
plt.ylabel("Total de Partidas Jogadas")
plt.title("Evolução de Partidas Jogadas por Década")

# Rotacionar os rótulos do eixo x para facilitar a leitura
plt.xticks(rotation=45, ha='right')

# Exibir o gráfico
plt.tight_layout()
plt.show()