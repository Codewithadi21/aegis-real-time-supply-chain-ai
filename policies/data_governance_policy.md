# Fictional supply-chain data governance policy

Synthetic policy example for the AEGIS portfolio; not a real company's policy.

Each sale event must include a globally unique event ID, timestamp, product ID, warehouse ID, currency, positive quantity and positive unit price. Event IDs must be deduplicated in reporting. Invalid events must be quarantined or excluded from curated facts with an auditable reason. Raw events must not be silently overwritten; transformations must be reproducible. Only synthetic data may be published in the public GitHub repository.
