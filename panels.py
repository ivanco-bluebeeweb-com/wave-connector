"""Panel UI for Wave Connector following UI_INTERFACE_STANDARD.md and AUTH_AND_CREDENTIALS_STANDARD.md."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext

def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings",
        variant="secondary",
        size="sm",
        icon="settings",
        on_click=ui.Call("__panel__wave_settings")
    )

def _help_modal() -> ui.UINode:
    return ui.Modal(
        trigger=ui.Button("How do I connect Wave?", variant="ghost", size="sm"),
        title="Connecting Wave Apps",
        children=[
            ui.Text(
                "1. Sign in to your Wave account at next.waveapps.com.\n"
                "2. Navigate to Manage your Profile > Integrations > API Access.\n"
                "3. Create a Full Access Token and copy it.\n"
                "4. Find your Business ID from your browser URL or Businesses list (encoded ID, e.g. QnVzaW5lc3M6...).\n"
                "5. Enter the Full Access Token and Business ID above and click Connect.",
                variant="body"
            )
        ]
    )

@ext.panel("wave_sidebar", slot="left")
async def wave_sidebar(ctx, **kwargs) -> ui.UINode:
    return ui.Stack(
        direction="v",
        gap=3,
        align="stretch",
        children=[
            ui.Text("Wave Accounting", variant="heading"),
            ui.Text("Manage invoices, customers, bills, bank accounts and tax rates via Wave GraphQL API.", variant="caption"),
            ui.Divider(),
            ui.Form(
                submit_label="Connect Wave",
                action=ui.Call("connect_wave"),
                children=[
                    ui.Stack(
                        direction="v",
                        gap=2,
                        align="stretch",
                        children=[
                            ui.Input(name="label", label="Connection Label", placeholder="e.g. My Freelance Business"),
                            ui.Input(name="access_token", label="Wave Full Access Token", placeholder="Wave API Access Token", password=True),
                            ui.Input(name="business_id", label="Business ID", placeholder="e.g. QnVzaW5lc3M6..."),
                            ui.Input(name="base_url", label="GraphQL Endpoint (Optional)", placeholder="https://gql.waveapps.com/graphql/public"),
                        ]
                    )
                ]
            ),
            ui.Divider(),
            ui.Stack(
                direction="v",
                gap=2,
                align="stretch",
                children=[
                    _help_modal(),
                    _settings_button()
                ]
            )
        ]
    )
