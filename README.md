# guardian-article-streamer

<details>
<summary>Table of Contents</summary>

1. [About The Project](#about-the-project) 
    - [Technologies Used](#technologies-used)
2. [Getting Started](#getting-started)  
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
3. [Usage](#usage)
4. [Contributor](#contributor)
5. [License](#license)
6. [Contact](#contact)
7. [Acknowledgements](#acknowledgements)

</details>

## About The Project

**Guardian Article Streamer** is a Python tool that fetches articles from the Guardian API based on search terms and publishes up to 10 of the most recent results to a message broker such as AWS Kinesis. Designed for integration with data platforms, it supports AWS Lambda deployment, adheres to PEP-8 standards, and securely manages API credentials via **AWS Secrets Manager**.

This application is designed to be highly modular, testable, and compliant with rate limits (max 50 requests/day).

### Technologies Used

**Runtime:**
- Python(3.X)
- Pydantic
- Requests
- Boto3
- python-dotenv

**Testing:**
- pytest
- moto
- isort
- black
- flake8

## Getting started

To get a local copy of this tool up and running, make sure all the prerequisites are met.

### Prerequisites

**These instructions assume that you already have python3 installed locally. If you do not, follow [this link](https://www.python.org/downloads/) to do so.**

- **AWS CLI:**

    Follow [this link](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) to get aws installed locally.
- **Virtual Enviroment (Recommended):**

    Use a virtual enviroment (venv) for dependency isolation. Follow [this link](https://docs.python.org/3/library/venv.html) for instructions.

### Installation
1. Fork and clone the repo.
```
git clone https://github.com/SelvitaPR/guardian-article-streamer.git
```

2. Configure AWS locally
   - On the AWS console, create a new IAM user for this pipeline, or use an existing one if you would like.
   - If you are creating a new user, follow the Principle of Least Privilege granting only the necessary permissions (e.g., secretsmanager:GetSecretValue, kinesis:PutRecords).
   - Once you have created the user, copy or save the access key and secret access key.
   - Run the command below and fill out any details it asks.
  ```
  aws configure
  ```

3. Install requirements and other dependencies. Run the following command in the activated venv.
```
pip install -r requirements. txt
```
4. In maintaining security, on the AWS console, set up the following secret in your AWS Secrets Manager (for primary credentials).
  - **Secret name**: guardian/article/streamer/api/credentials
  - **key/pair values**:

      GUARDIAN_API_KEY=**** 

      GUARDIAN_URL=**** 

     You can get API credentials at [The Guardian API](https://open-platform.theguardian.com/access/).



5. **Configure local enviroment**. Create a file named .env at the project root for non-sensitive configuration values.
```
# --- Local Configuration for CLI Execution ---
# These are used for initializing the publisher and locating the secret.

SECRET_NAME=guardian/article/streamer/api/credentials
KINESIS_REGION=eu-west-2
KINESIS_STREAM_NAME=guardian-article-stream
```
 
## Usage 
You can run the application directly from the command line, which initiates the fetch from the Guardian API and attempts to publish the results to the Kinesis stream defined in your AWS account.

**Execute the main CLI script:**
```
# Example 1-> Search for 'machine learning' from a specific date:
python -m src.cli --search "machine learning" --date_from "2024-01-01"

# Example 2-> Search for 'bitcoin' using today's date (since --date_from is optional):
python -m src.cli --search "bitcoin" 
```

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
