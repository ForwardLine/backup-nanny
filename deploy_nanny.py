import click

from backup_nanny.util.env_loader import ENVLoader
from buildlib.helpers.logging_helper import LoggingHelper as Log
from buildlib.nanny_deployer import NannyDeployer

@click.command()
@click.option('--region', help='AWS region that your Pipeline will be deployed to. Defaults to the region you are authenticated to. If you receive a region error during deploy, you can pass this variable or set up your ~/.aws/config default region.', required=False)
@click.option('--use-previous-value', help='If you are redeploying the Pipiline, you can pass this as False if you need to deploy different variables from your .env file', required=True, type=bool, default=True, show_default=True)
def cli(region, use_previous_value):
    Log.setup_logging()
    ENVLoader.run()
    nanny_deployer = NannyDeployer(region=region, use_previous_value=use_previous_value)
    nanny_deployer.deploy()


if __name__ == '__main__':
    cli()
