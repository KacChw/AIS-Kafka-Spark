import pandas as pd

# Tworzymy przykładową tabelę (DataFrame)
dane = {
    "id": [1, 2, 3],
    "imie": ["Anna", "Jan", "Kasia"],
    "miasto": ["Warszawa", "Kraków", "Gdańsk"],
}
df = pd.DataFrame(dane)

# Zapisujemy do formatu Parquet z kompresją Snappy
df.to_parquet("osoby.parquet", compression="snappy")
