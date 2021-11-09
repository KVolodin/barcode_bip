# barcode_bip - generator qrcode and barcode
Instruction:

Tested on packages:
pdf417         0.8.1
Pillow         8.4.0
python-barcode 0.13.1
qrcode         7.3.1

1. Run qrcode_generator.py -t "40900411111::upc::Billa" "77897770163499::pdf417::Ashan" "https://github.com/KVolodin/::qrcode::Github"
2. Run build.bat
3. Flash elf file

Format comand line:
code::type::name ( '::' is delimeter)

Avalible types:
pdf417
qrcode
ean8
ean13
ean
gtin
ean14
jan
upc
upca
isbn
isbn13
gs1
isbn10
issn
code39
pzn
code128
itf
gs1_128