# F1Analisys

<img src="./img/plot_example.png" alt="" width="500" height="400">

F1 proyect to analyze the data of the F1 championship making use of the pandas library to handle the data and the matplotlib library to plot different analisys like:

- Track dominance
- Top speed
- Lap time average
- Race pace
- Team performance
- Fastest laps
- Race position evolution
- Fatest drivers each compound

## Instalation

To install the repository, you can make a fork of the repository or cloning my repository using the following command:

```commandline
git clone git@github.com:Maxbleu/F1Analisys.git
```

Later , you can install the required libraries using pip with the following command:

```commandline
pip install -r requirements.txt
```

### Run

To run the proyect, you need to execute the following command:

```commandline
python -m uvicorn main:app --reload
```


## Usage

This proyect is designed to get every analisys named before for normal persons out of the tech word interested in the technical part of F1 and developers.

In every endpoint of this proyect, after the url, you can put if you want convert the image to bytes or not, if you don't want to convert the image to bytes, you need to put `?convert_img=False` in the url, because, this option is enabled by default. 

### `/analisys/track_dominance/2024/10/Q?convert_img=False`
In this case the url would be: [this example](https://f1analisys-production.up.railway.app/analisys/track_dominance/2024/10/Q?convert_img=False)

<img src="./img/example_get_image_not_converted.png" alt="ejemplo de obtener un analisis sin convertir a bytes">

### `/analisys/track_dominance/2024/10/Q?convert_img=True`
In this case the url would be: [this example](https://f1analisys-production.up.railway.app/analisys/track_dominance/2024/10/Q)

<img src="./img/example_get_image_converted.png" alt="ejemplo de obtener un analisis convertido a bytes">

## Coming soon

- [ ] Laps comparation in specific session
- [ ] Average usage throtel
- [ ] Average usage brake
- [ ] Make new things with IA and ML to analize the data and
make predictions.

## Special mention
I want to thank to Fastf1 proyect for the data, and to the F1 community for the passion and the love for the sport.
If that proyect don't exist, this proyect wouldn't exist. I only have one word in my mind: THANK YOU.

## Contributing

For contributing to this proyect, you need to read first of all [CONTRIBUTING.md](https://github.com/Maxbleu/F1Analis/CONTRIBUTING.md)

## Notice
F1Analisys is unofficial and are not associated in any way with the Formula 1 companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks are trade marks of Formula One Licensing B.V.
