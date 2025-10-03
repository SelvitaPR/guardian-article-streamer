#entry point for lambda
#Responsibility: Same orchestration as cli.py, but triggered by AWS.
#Keep it thin — it should just parse the Lambda event, call into your existing functions, and return a response.