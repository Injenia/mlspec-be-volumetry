# Volumetria back-end

## Init

- Create & activate a virtualenv python3.7
- Run those commands:
    ```bash
    pip install poetry==1.1.7
    poetry install
    bash scripts/download_model.sh 
    ```

## Run the back-en locally

- Bash:
    ```bash
    bash scripts/serve
    ```

- Python:
    ```bash
    cd src && export PYTHONPATH="$PWD" && python be_volumetria/main.py
    ```

## .env file

- \src\.env
    - Structure:
      ```text
      DEBUG="False"
      ```
