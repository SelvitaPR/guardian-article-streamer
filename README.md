# guardian-article-streamer

<details>
<summary>Table of Contents</summary>

1. [About The Project](#about-the-project) 
    - [Built With](#built-with)
2. [Getting Started](#getting-started)  
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
3. [Contributor](#contributor)
4. [License](#license)
5. [Contact](#contact)
6. [Acknowledgements](#acknowledgements)

</details>

## About The Project

Guardian Article Streamer is a Python tool that fetches articles from the Guardian API based on search terms and publishes up to 10 of the most recent results to a message broker such as AWS Kinesis. Designed for integration with data platforms, it supports AWS Lambda deployment, adheres to PEP-8 standards, and securely manages API credentials.

### Built And Test With
- Python
- Pydantic
- Boto3
- isort
- black
- flake8

## Getting started

To get a local copy of this tool up and running, make sure all the prerequisites are met.

### Prerequisites

**These instructions assume that you already have python3 installed locally. If you do not, follow [this link](https://www.python.org/downloads/) to do so.**

- **aws**

    Follow [this link](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) to get aws installed locally.

### Installation
1. Fork and clone the repo.
```
git clone https://github.com/SelvitaPR/guardian-article-streamer.git
```

2. Configure AWS locally
   - On the AWS console, create a new IAM user for this pipeline, or use an existing one if you would like.
   - If you are creating a new user, follow the Principle of Least Privilege. Only give permissions for the resources you see in the project's terraform directory.
   - Once you have created the user, copy or save the access key and secret access key.
   - Run the command below and fill out any details it asks.
  ```
  aws configure
  ```

3. Install requirements and other dependencies. It is highly recommended to work in a virtual enviroment (venv). Follow [this link](https://docs.python.org/3/library/venv.html) for instuctions. Finally, run the following command in the activated venv.
```
pip install -r requirements. txt
```
4. If you are making any changes to the code or testing it locally, add the following to your .env file.
```
GUARDIAN_API_KEY=**** 
GUARDIAN_URL=**** 
SECRET_NAME=****
KINESIS_REGION=****
KINESIS_STREAM_NAME=****
```
You can get API credentials at [The Guardian API](https://open-platform.theguardian.com/access/). You will also need these for step 5.

5. In maintaining security, set up the following secret in your AWS Secrets Manager.
  - **Secret name**: guardian/article/streamer/api/credentials
  - **key/pair values**:

      GUARDIAN_API_KEY=**** 

      GUARDIAN_URL=**** 

## Contributor

Don't forget to give the project a star! Thank you.

<table border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td align="center">
      <a href="https://github.com/SelvitaPR">
        <img src="https://avatars.githubusercontent.com/SelvitaPR" width="60" height="60" alt="SelvitaPR"/>
        <br />
        <sub><b>SelvitaPR</b></sub>
      </a>
    </td>
  </tr>
</table>

## License

This project is licensed under the MIT License.

## Contact

If you have any questions or would like to collaborate, contact me on:
Patricia Selva Plaza Rojas - [selva.pla.roj@gmail.com](mailto:selva.pla.roj@gmail.com)

## Acknowledgements 

I am grateful to [Tech Returners](https://www.techreturners.com/) for trusting me with this project.
