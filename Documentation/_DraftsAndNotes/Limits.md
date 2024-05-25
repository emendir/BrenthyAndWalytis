get_time_stamp(datetime) won't work for years greater than  around 10^17 or something like that cause of the datetime function and the inability of to_b255_no_0s(number) to process such large numbers
Block IDs may also not be greater than this number
