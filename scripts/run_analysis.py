from friction_lab.metrics import build_analysis_artifacts

if __name__ == "__main__":
    summary = build_analysis_artifacts()
    for key, value in summary.items():
        print(f"{key}: {value}")
