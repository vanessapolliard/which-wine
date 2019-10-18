# Which Wine?

Being an avid wine-drinker I always find myself staring at the wall of wine without much direction in which wine to choose. I typically stick to the varieties I know I like, but what if I could find exact wines that match my tastes based on professional wine taster reviews?

## Data Processing
<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/rawdata.png">
</p>
I found a dataset on Kaggle scraped from Wine Enthusiast including ~150,000 wine reviews from 19 wine tasters logging reviews with detailed descriptions, scores, prices, and other metadata. The raw data was fairly clean upon import - not a significant amount of NaNs and no NaN in the description attribute. There were special characters from text written in other languages that had to be cleaned. 

## Data Analysis
<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/ratings.png">
</p>
Seems like wine reviewers are hesitant to rate a wine a score of 89.

<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/pricebyscore.png">
</p>
Median wine prices increase drastically in the high 90's.

<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/varieties.png">
</p>
I expected a more flat distribution of varieties being reviewed, but I was surprised to find Pinot Noir and Chardonnay with the most reviews.

<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/vintageyears.png">
</p>
Vintage years of the wines reviewed ranged from 1904 to 2018.

## Topic Modeling
I used an LDA (Latent Dirichlet Allocation) model to categorize the data with a term-frequency bag of words matrix. I also tried NMF (Non-negative Matrix Factorization) with a TF-IDF (inverse document frequency) matrix, but because of the nature of the description text wines were classified in a strange manner.

I used english stop words and added additional words that weren't helpful in the model. I chose to use the Wordnet lemmatizer because when testing it against snowball and porter stemmers less connotation was lost.

Additional stop words: wine, flavor, aromas, finish, palate, note, nose, drink, fruit, like

<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/wordcounthist.png">
</p>

<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/ratingwordcnt.png">
</p>

### Topics

**Fresh & Fruity** - acidity, fresh, apple, crisp, ripe, blend, tannins, citrus, spice, fruity

**Berry Blend** - cherry, blackberry, cabernet, black, blend, spice, tannins, sweet, acidity, merlot

**Tart Citrus** - white, acidity, peach, lemon, fresh, apple, pear, citrus, offer, body

**Dark & Juicy** - tannins, black, cherry, ripe, rich, acidity, dark, spice, berry, texture

**Dark Berries & Spice** - black, cherry, tannins, acidity, berry, offer, spice, ripe, pepper, fresh

**Full & Smokey** - ripe, rich, tannins, acidity, structure, black, balance, wood, texture, spice

**Warm Spice** - berry, tannins, acidity, plum, spice, cherry, vanilla, feel, herbal, good

<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/topic0words.png">
</p>

<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/topic6words.png">
</p>

### Model Scores
**log perplexity** = -7.10
**coherence** =  0.35

## Next Steps
