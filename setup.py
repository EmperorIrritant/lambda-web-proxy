import boto3

LambdaFunctionExecutionRole = "LambdaWebProxyRole"
LambdaFunctionExecutionRoleDescription = "Lambda Execution Role that intends to allow nothing, but has to allow/deny something so allows listing tags which will not be done."
LambdaFunctionName = "webproxy"
LambdaFunctionRuntime = "python3.9"
LambdaFunctionHandler="lambda_handler"
LambdaFunctionDescription="Lambda function to act as a web proxy"
LambdaFunctionTimeout=5
LambdaFunctionMemorySize=128        # TODO Benchmark with https://github.com/byrro/awslambda-memory-tradeoff or dashbird.io: 3 different sized pages, upto 3GB of memory sizes, both architectures
LambdaFunctionPublish=True
LambdaFunctionDeploymentPackageType="Zip"
LambdaFunctionTags={
    "Project": "Lambda Web Proxy"
}
LambdaFunctionLayers=[
    LambdaBS4LayerName
]
LambdaFunctionArchitecture="x86_64"

LambdaBS4LayerName="BeautifulSoup4"
LambdaBS4LayerDescription="BeautifulSoup4 v4.10.0"
LambdaBS4LayerRuntimes=[
    LambdaFunctionRuntime
]

LambdaRequestsLayerName="BeautifulSoup4"
LambdaRequestsLayerDescription="BeautifulSoup4 v4.10.0"
LambdaRequestsLayerRuntimes=[
    LambdaFunctionRuntime
]

def get_deployment_package():
    pass

def get_bs4_layer():
    pass

def get_requests_layer():
    pass

iam = boto3.client('iam')
awslambda = boto3.client('lambda')

with open("lambda-execution-policy.json") as policy_file:
    LambdaFunctionExecutionRolePolicy = policy_file.read().strip()

iam_role = iam.create_role(
    RoleName=LambdaFunctionExecutionRole,
    AssumeRolePolicyDocument=LambdaFunctionExecutionRolePolicy,
    Description=LambdaFunctionExecutionRoleDescription
)

lambda_bs4_layer = awslambda.publish_layer_version(
    LayerName=LambdaBS4LayerName,
    Description=LambdaBS4LayerDescription,
    Content={
        'ZipFile': get_bs4_layer()
    },
    CompatibleRuntimes=LambdaBS4LayerRuntimes,
    LicenseInfo='MIT',              # BeautifulSoup4 License
    CompatibleArchitectures=[
        'x86_64',
        'arm64',
    ]
)

lambda_requests_layer = awslambda.publish_layer_version(
    LayerName=LambdaRequestsLayerName,
    Description=LambdaRequestsLayerDescription,
    Content={
        'ZipFile': get_requests_layer()
    },
    CompatibleRuntimes=LambdaRequestsLayerRuntimes,
    LicenseInfo='Apache-2.0',              # Python-Requests License
    CompatibleArchitectures=[
        'x86_64',
        'arm64',
    ]
)

lambda_function = awslambda.create_function(
    FunctionName=LambdaFunctionName,
    Runtime=LambdaFunctionRuntime,
    Role=LambdaFunctionExecutionRole,
    Handler=LambdaFunctionHandler,
    Code={
        'ZipFile': get_deployment_package()
    },
    Description=LambdaFunctionDescription,
    Timeout=LambdaFunctionTimeout,
    MemorySize=LambdaFunctionMemorySize,
    Publish=LambdaFunctionPublish,
    PackageType=LambdaFunctionDeploymentPackageType,
    DeadLetterConfig={}                                         # Maybe later, for testing?
    Environment={
        "Variables": ""
    },
    Tags=LambdaFunctionTags,
    Layers=LambdaFunctionLayers,
    Architecture=LambdaFunctionArchitecture
)