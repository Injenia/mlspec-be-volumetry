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

# Tips

## Jupyter lab on VM
- Start the cloud engine VM 
- Run the jupyter service (`jupyter lab` command)
- Connect in port forward the local machine to the remote VM.
  - In the example the VM is `api-testing-vm`:
        ```
        gcloud compute ssh api-testing-vm --zone us-central1-a -- -NL 8888:localhost:8888
        ```
- Connect to `localhost:8888`
