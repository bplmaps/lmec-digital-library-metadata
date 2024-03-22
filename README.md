# lmec-digital-library-metadata

This is a Git repository for tracking changes to the [Leventhal Map & Education Center](https://leventhalmap.org)'s library of digital assets.

Note that it is distinct from [bplmaps/metadata](https://github.com/bplmaps/metadata), which is the live repository of record for the LMEC's [Public Data Portal](https://data.leventhalmap.org/#/).

### What's here?

* `/atlascope`: Volume extent files for Atlascope instances
* `/allmaps`: Bulk data exports from Allmaps Annotations API

### Updating metadata for Atlascope

* Download latest copy of `boston-geojson-extents.geojson` from Wasabi
* Add metadata new atlas layer under `features`
* Commit and merge back into this Git repository
* Test with local [Atlascope](https://github.com/bplmaps/atlascope-v2) by pointing ID to the raw GitHub source (example here)
* Tag someone in a GitHub issue to confirm 2 people have looked at it
* Once it's approved, paste it back into Wasabi
