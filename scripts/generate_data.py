from friction_lab.generate import generate_datasets

if __name__ == "__main__":
    paths = generate_datasets()
    print(f"Generated {paths.applications}")
    print(f"Generated {paths.events}")
