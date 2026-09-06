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
                            ui.Stack(
                                direction="v",
                                gap=1,
                                align="stretch",
                                children=[
                                    ui.Text("Connection Label", variant="label"),
                                    ui.Input(param_name="label", placeholder="e.g. My Freelance Business"),
                                ]
                            ),
                            ui.Stack(
                                direction="v",
                                gap=1,
                                align="stretch",
                                children=[
                                    ui.Text("Wave Full Access Token", variant="label"),
                                    ui.Input(param_name="access_token", placeholder="Paste your Wave Full Access Token"),
                                ]
                            ),
                            ui.Stack(
                                direction="v",
                                gap=1,
                                align="stretch",
                                children=[
                                    ui.Text("Business ID", variant="label"),
                                    ui.Input(param_name="business_id", placeholder="e.g. QnVzaW5lc3M6..."),
                                ]
                            ),
                            ui.Stack(
                                direction="v",
                                gap=1,
                                align="stretch",
                                children=[
                                    ui.Text("GraphQL Endpoint (Optional)", variant="label"),
                                    ui.Input(param_name="base_url", placeholder="https://gql.waveapps.com/graphql/public"),
                                ]
                            ),
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
