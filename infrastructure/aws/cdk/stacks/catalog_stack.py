from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as ecr,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    CfnOutput
)
from constructs import Construct

class CatalogStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "CatalogVPC",
            max_azs=2,
            nat_gateways=1
        )

        # Create ECR Repository
        repository = ecr.Repository(self, "CatalogRepository",
            repository_name="catalog-api",
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create ECS Cluster
        cluster = ecs.Cluster(self, "CatalogCluster",
            vpc=vpc,
            cluster_name="catalog-cluster"
        )

        # Create RDS Instance
        database = rds.DatabaseInstance(self, "CatalogDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_14
            ),
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            database_name="ioet_catalog_db",
            credentials=rds.Credentials.from_generated_secret("postgres"),
            multi_az=False,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False
        )

        # Create Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "CatalogService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(repository),
                container_port=8000,
                environment={
                    "DATABASE_URL": f"postgresql://postgres:{database.secret.secret_value_from_json('password')}@{database.instance_endpoint.hostname}/ioet_catalog_db"
                }
            ),
            public_load_balancer=True
        )

        # Allow the Fargate service to access the RDS instance
        database.connections.allow_from(
            fargate_service.service,
            ec2.Port.tcp(5432),
            "Access from Fargate Service"
        )

        # Output values
        CfnOutput(self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )
        CfnOutput(self, "ECRRepository",
            value=repository.repository_uri
        )
