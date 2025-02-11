#!/usr/bin/env python3
from aws_cdk import App, Environment
from stacks.catalog_stack import CatalogStack

app = App()

CatalogStack(app, "CatalogStack",
    env=Environment(
        account="ACCOUNT_ID",  # Replace with your AWS account ID
        region="us-west-2"     # You can change the region as needed
    )
)

app.synth()
