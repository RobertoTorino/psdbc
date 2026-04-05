# import chardet

# with open('C:/TE7/AMCUS/AMConfig.ini', 'rb') as f:
#     raw_data = f.read()
#     result = chardet.detect(raw_data)
#     print(result)

encodings = ['euc-kr', 'shift-jis', 'utf-8']
for enc in encodings:
    try:
        with open('C:/TE7/AMCUS/AMConfig.ini', encoding=enc) as f:
            print(f.read())
            break  # Stop if we find the correct encoding
    except UnicodeDecodeError:
        continue
