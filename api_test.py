import os
import requests

API_URL = "http://localhost:8000/pdfs/upload"
CONTENT_DIR = "content"


def collect_pdfs(folder: str):
    files = []

    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(folder, filename)

            files.append(
                (
                    "files",  # must match FastAPI parameter name
                    (
                        filename,
                        open(path, "rb"),
                        "application/pdf",
                    ),
                )
            )

    return files


def main():
    files = collect_pdfs(CONTENT_DIR)

    if not files:
        print("No PDFs found in content/")
        return

    response = requests.post(API_URL, files=files)

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())


if __name__ == "__main__":
    main()