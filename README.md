## Direct Sun Hours App

![App](/images/app.png)

## Notes

### Settings

Setup your project folder:

1. Go to [Pollination Cloud / projects](https://app.pollination.cloud/projects)
2. Select the project where you want to run your simulation
3. Click on `Settings/Recipes`
4. Add `ladybug-tools/direct-sun-hours:0.5.4`

### Login

Provide a pollination cloud API key, username and project name (e.g. demo)

### Run simulation

If you are using the browser;

1. Upload a hbjson file
2. Upload an EPW file
3. Run the simulation

### Read results

1. Go to [Pollination Cloud / projects](https://app.pollination.cloud/projects)
2. Select a project where a 'direct sun hours' job without recipe `-viz` is
3. Open the project
4. Copy the URL (E.g. `https://app.pollination.cloud/antonellodinunzio/projects/demo/jobs/acc403cf-c81a-4ca6-a9d5-cf48a77a01f2`)
5. Delete the 'projects' keyword from the path (E.g. `https://app.pollination.cloud/antonellodinunzio/demo/jobs/acc403cf-c81a-4ca6-a9d5-cf48a77a01f2`) and copy it
6. Paste it inside JOB ID streamlit input

## To run the app locally

- Clone the repo locally, go into the directory and run the following commands;

- `pip install -r requirements.txt`

- `streamlit run app.py`
