from src.ingestion.cuad_loader import CUADLoader

loader = CUADLoader()

dataset_path = r"C:\Users\Admin\Desktop\ZAALIMA TEAM\CUAD DATASET\cuad-main\data\CUADv1.json"

contracts = loader.load(dataset_path)

print("Total parsed contracts:", len(contracts))

print("\nFirst Contract Title:")
print(contracts[0]["title"])

print("\nContext Length:")
print(len(contracts[0]["context"]))

print("\nNumber of QAs:")
print(len(contracts[0]["qas"]))