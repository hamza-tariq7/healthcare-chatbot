# Synthetic operational data

The generator creates these related tables:

| Table | Default rows | Key and relationship |
| --- | ---: | --- |
| drug_master.csv | 8,000 | drug_id identifies a simulated catalog entry |
| locations.csv | 80 | location_id identifies a simulated storage location |
| cost_contracts.csv | 8,000 | drug_id links to the catalog |
| inventory_lots.csv | 200,000 | inventory_id identifies a lot record; drug_id and location_id link to the other tables |

Catalog fields include generic/brand-like names, strength, form, route, controlled_flag, refrigerated_flag, and a synthetic ob_group_key. That group key is a hash of catalog attributes, not an FDA therapeutic-equivalence code.

Lot fields include quantity, unit, status, expiration date, par level, reorder point, and update time. Location fields include facility, area, temperature zone, and access-level labels. Contract fields include unit_cost, vendor, contract dates, and a GPO flag. Access-level labels are data fields rather than implemented permissions.

All operational records and prices are simulated. Generate the full data locally with scripts/generate_synthetic_data.py. Generated CSVs are ignored by git. The package does not include hospital or patient records.
