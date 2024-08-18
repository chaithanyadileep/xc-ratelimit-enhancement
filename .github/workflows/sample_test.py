name: "Python Basic Test"

on:
  push:
    branches:
      - main
  pull_request:
  workflow_dispatch:

jobs:
  update_Ip_addr_in_cloud:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./python
    steps:
    # Installing python for Validation 
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v3
      
    # Install the necessary Packages
    - name: Install the necessary packages
      run: |
        python -m pip install requests      
        
    - name: Updating the IP
      run: |
        python cloud-api-vars.py

    - name: Validate Deployment  
      run: |
        if [ ${{ env.EXIT }} == "true" ]; then echo "application deployment unsuccessful or application not reachable"; exit 1;\
        else echo "deployment is successfull"; fi