# src/music_manager/cli/support_commands.py

import click
import webbrowser
import logging

# -----------------------------------------------------------------------------
# Support Command
# -----------------------------------------------------------------------------

@click.command(name="support", help="Get help and community support information.")
@click.pass_context
def support_command(ctx):
    """
    Provides users with support information, including a link to the
    official Discord server for community help and discussion.
    """
    logger = ctx.obj['logger']
    config_manager = ctx.obj['config']
    
    try:
        # Retrieve the Discord URL from the configuration
        # This makes the link easy to update without changing the code.
        support_section = config_manager.get_section("support")
        discord_url = support_section.get("discord_invite_url") if support_section else None

        # Check if the URL is configured and not just a placeholder
        if not discord_url or "YOUR_INVITE_CODE" in discord_url:
            click.echo("Support information has not been configured by the application owner.")
            logger.warning("Support command called, but 'discord_invite_url' is not set in config.toml.")
            return

        # Display the support message
        click.echo("="*50)
        click.secho("Support & Community", fg="cyan", bold=True)
        click.echo("\nFor help, bug reports, feature requests, or to join the community,")
        click.echo("please visit our official Discord server.")
        
        # Use click.style for a consistent look and feel
        click.echo(f"\nDiscord Invite Link: {click.style(discord_url, fg='green')}\n")
        
        # Ask the user if they want to open the link directly in their browser
        if click.confirm("Do you want to open this link in your web browser now?"):
            try:
                webbrowser.open(discord_url, new=2)
                click.echo("Opening the link in your default browser...")
            except Exception as e:
                # Handle cases where a browser might not be available (e.g., pure SSH session)
                logger.error(f"Could not automatically open the web browser: {e}")
                click.echo("Could not automatically open the browser. Please copy the link manually.")
        
        click.echo("="*50)

    except KeyError:
        # This handles the case where the entire [support] section is missing
        click.echo("The '[support]' section is missing from your config.toml file.")
        logger.warning("Support command called, but '[support]' section not found in config.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the support command: {e}", exc_info=True)
        click.echo("An unexpected error occurred while trying to get support information.")