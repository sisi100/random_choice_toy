import os

from aws_cdk import aws_events, aws_lambda, core
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda_python import PythonFunction
from aws_cdk.aws_s3 import BlockPublicAccess, Bucket
from aws_cdk.aws_s3_deployment import BucketDeployment, Source

APP_NAME = "RandomChoiceToy"


class LambdaLayerStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3
        bucket = Bucket(
            self,
            f"{APP_NAME}Bucket",
            block_public_access=BlockPublicAccess(
                block_public_acls=True, block_public_policy=True, ignore_public_acls=True, restrict_public_buckets=True
            ),
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        BucketDeployment(
            self, f"{APP_NAME}Images", sources=[Source.asset("images")], destination_bucket=bucket,
        )

        # lambda
        lambda_ = PythonFunction(
            self,
            f"{APP_NAME}Lambda",
            entry="app",
            handler="random_choice",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            timeout=core.Duration.seconds(10),
            memory_size=128,
            environment=dict(
                BUCKET=bucket.bucket_name,
                SLACK_URL="https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX",  # MEMO: ここにSlackの`Webhook URL`を書き込む
            ),
        )

        # cronの設定
        aws_events.Rule(
            self,
            f"{APP_NAME}EventBridgeMorning",
            schedule=aws_events.Schedule.cron(minute="0", hour="21", month="*", week_day="*", year="*"),  # JSTの6:00に起動
        ).add_target(LambdaFunction(lambda_))

        # 権限周り
        bucket.grant_read(lambda_)


app = core.App()
env = core.Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION"))

# Stacks
LambdaLayerStack(app, APP_NAME, env=env)

app.synth()
