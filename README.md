# Volumetry back-end
> Serve an images classification ML model (TensorFlow) exposing a back-end API (FastAPI)

## Back-end setup

### Requirements

- `gsutil` command installed
  - Tip: [offical guide](https://cloud.google.com/storage/docs/gsutil_install)
- `~python3.7` installed with `poetry`
  - Tip: install poetry using `$ pip install poetry==1.1.7`

### Download the model
- Download the ML model from GCS:
  - Check the ML model info from `/src/ml_models/model_info.json`
  - Download the model:
    ```bash
    $ bash scripts/download_model
    ```
### Install the dependencies
- Run this command:
    ```bash
    $ poetry install
    ```
### `.env` file
- Used to set back-end parameters
- Copy the file `src/.env-example` > `src/.env` and fill the values according to your requirements


### Run the back-end locally
- Start the back-end:
    ```bash
    $ bash scripts/serve
    ```
- Visit the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

### Test the docker image
- Build the images using:
  - `$ bash ci/01_build.sh`
  - Note: you must have downloaded the ml before build the docker image

## Back-end deploy
- Push the changes to the main git branch named `master`
  - Tip: work on a branch and then merge the changes
- This process will trigger a _cloud build_ pipeline
  - The pipeline will build a back-end docker image and update the associated [_cloud run_](https://console.cloud.google.com/run/detail/europe-west1/cloudrun-be-volumetry/metrics?project=mlteam-ml-specialization-2021)
  - Tip: the pipeline steps are described on the `/ci/yaml/cloudbuild.yaml` file


## Back-end test
- Run the jupyter notebook `notebooks/api_caller.ipynb` and follow the instructions
  - Note: a GCP account with _Cloud Run Invoker_ role is required
  - Tip: on GCP is deployed a [compute engine vm](https://console.cloud.google.com/compute/instancesDetail/zones/us-central1-a/instances/api-testing-vm?project=mlteam-ml-specialization-2021&rif_reserved) with custom service account tailored to run the notebook