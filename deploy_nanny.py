import click
from dotenv import load_dotenv

from buildlib.helpers.logging_helper import LoggingHelper as Log
from buildlib.nanny_deployer import NannyDeployer

@click.command()
@click.option('--stack-name', help='', required=True)
@click.option('--region', help='', required=True, default='us-west-2', show_default=True)
@click.option('--use-previous-value', help='', required=True, type=bool, default=True, show_default=True)
def cli(stack_name, region, use_previous_value):
    Log.setup_logging()
    load_dotenv()
    nanny_deployer = NannyDeployer(stack_name=stack_name, region=region, use_previous_value=use_previous_value)
    nanny_deployer.deploy()


if __name__ == '__main__':
    cli()
