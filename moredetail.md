
The base layout for a Hashlet Solo entry looks like
>Device DeviceName (DeviceType)
>Power: Value in GH or MH
>BTC Payout: Value
>Maintenence Fee: Value

>Mined Pool - Actual BTC Mined - Date

A Hashlet Prime due to HashPoints and Double Dipping has the ability to provide extended information
>Device DeviceName (DeviceType)
>Power: Value in GH or MH
>BTC Payout: Value
>HP Payout: Value
>Maintenence Fee: Value

>Mined Pool - Actual BTC Mined - Date
>Double Dip Mined Pool - Actual BTC Mined - Date

It may seem that the record of BTC mined is displayed twice. It is not. The bottom field provides discrete information about the performance of each pool when double dipping. Additionally, it serves as a record for when your miner's payout is more than the day's maintenance fee. The top "BTC Payout" field will display 0.01 microBTC+maintenance fee, while the bottom field will display the amount you actually mined.

The script automatically parses each entry uniquely regardless of format.
