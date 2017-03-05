# bovespatools

A set of tools for crawling the Bovespa stock exchange data, and plotting charts with the stored data.

## Usage
* `update_database.sh <year>` Fetches the quotes for the specified year.
* `browse_assets.py` Opens an interactive plot of assets of interest. Use the arrow keys <left> and <right> to browse through assets.
* `update_corporate_actions.py` Fetches the corporate actions (dividends, splits and joins) for all assets.
