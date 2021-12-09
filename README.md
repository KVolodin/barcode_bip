# barcode_bip - generator qrcode and barcode
Instruction:

Tested on packages:<br />
pdf417         0.8.1<br />
Pillow         8.4.0<br />
python-barcode 0.13.1<br />
qrcode         7.3.1<br />

1. Run qrcode_generator.py -t "40900411111::upc::Billa" "77897770163499::pdf417::Ashan" "https://github.com/KVolodin/::qrcode::Github"
2. Flash elf file

Format comand line:<br />
code::type::name ( '::' is delimeter)

Avalible types:<br />
pdf417<br />
qrcode<br />
ean8<br />
ean13<br />
ean<br />
gtin<br />
ean14<br />
jan<br />
upc<br />
upca<br />
isbn<br />
isbn13<br />
gs1<br />
isbn10<br />
issn<br />
code39<br />
pzn<br />
code128<br />
itf<br />
gs1_128<br />