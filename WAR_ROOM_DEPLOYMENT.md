# SICE War Room Deployment and Operation

## Delivered Module

The new **`SICE_WAR_ROOM.html`** module is a no-scroll operational wall display for a spare monitor. It reads the existing portal’s shared local browser data and does not create, replace, or seed operational records. It was built for the existing dark charcoal/steel SICE visual system and is automatically refreshed every 45 seconds, with immediate updates when another open SICE page changes one of its source records.

| Display area | Existing live source | Behaviour |
|---|---|---|
| Site map with pins | `sice_premises_log`, `sice_hs_hazards`, `sice_patrol_scans`, and `sice_activity_log` | Reuses the existing premises/hazard rules and reconnects APS/Unit 13 pins to patrol-scan evidence where a checkpoint mapping exists. |
| Real-time activity ticker | `sice_activity_log` | Shows the newest 20 cross-module events and gently auto-scrolls only when the list exceeds the ticker window. |
| Open hazards | `sice_hs_hazards` | Counts records not marked `closed`, matching the SOC status-strip logic. |
| Keys currently out | `sice_key_assets` | Counts assets whose status is `out`, matching the SOC status-strip logic. |
| Patrol status | `sice_patrol_scans` | Shows the newest checkpoint and time since the scan. A scan older than 24 hours is shown as a watch condition. |
| Flagged / incident count | `sice_activity_log` | Counts `fail` and `incident` entries from the last 24 hours, matching the SOC status-strip logic. |
| Expiry watchlist | Vehicle, fleet, and personal expiry records | Shows the three most urgent items that are expired or due in the next 30 days. |

The display border follows the portal’s priority logic. **Red** means there is at least one open hazard or 24-hour flagged/incident event. **Amber** means there is no red condition but keys are out or expiry items are due. **Green** means the status-strip exceptions are clear.

## Portal Integration

`SICE_SOC_MAIN.html` now contains a top-level War Room card and a quick-action button. The allocated shortcut is **20**: type **`2` then `0` within 0.7 seconds**. This preserves the existing standalone `2` key shortcut for Key Control; pressing only `2` opens Key Control after the short sequence window.

The module must be opened from the same Linux browser profile and the existing local SICE server origin. This is necessary because the current portal shares live information through the browser’s local storage. If the display opens before source modules have written their records, it deliberately shows the relevant `Negative. No ...` state rather than placeholder data.

## Linux Installation

Extract the updated archive over the active SICE Portal Hub directory while the portal server is stopped. Preserve the existing directory path expected by `launch_sice_portal.sh`:

```text
/home/philip/Desktop/OPS MAIN/SOC CENTRE/SICE PORTAL HUB
```

Start the portal through the existing launcher:

```bash
cd "/home/philip/Desktop/OPS MAIN/SOC CENTRE/SICE PORTAL HUB"
./launch_sice_portal.sh
```

Then sign into the main portal and use **Open War Room**, the new carousel card, or the `20` shortcut. The existing local server serves the module at:

```text
http://127.0.0.1:8743/SICE_WAR_ROOM.html
```

For the spare monitor, open the War Room in a dedicated browser window and use the browser’s full-screen mode. Do not open it directly with `file://`, because the portal’s existing local data and service-worker behaviour are designed for the local HTTP server.

## Validation Record

The supplied project was preserved before editing with `SICE_SOC_MAIN.html.pre_war_room.bak`. The new module and updated portal scripts passed embedded JavaScript syntax checks. The local SICE server returned HTTP 200 for both the War Room and the portal shell; the War Room was rendered at 1920×1080 and verified as a three-column, no-page-scroll display. See `../validation_findings.md` in the delivery workspace for the detailed sandbox validation record.

## Claude Key Preparation

No Claude credential has been inserted into the portal. Complete `CLAUDE_SETUP.md` on the Linux host only when ready to start the separate AI Summary module. The Anthropic API key must be created by the account owner in the Claude Console and is displayed in full only when it is created.[1] The later AI Summary route will keep the credential server-side; the browser must never receive it.[1] [2]

## References

[1]: https://platform.claude.com/docs/en/get-api-key "Anthropic: Get your Claude API key"
[2]: https://platform.claude.com/docs/en/api/overview "Anthropic: API overview and authentication"
