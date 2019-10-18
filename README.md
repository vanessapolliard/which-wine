# Which Wine?

Being an avid wine-drinker I always find myself staring at the wall of wine in the liquor store without much direction in which wine to choose. I typically stick to the varieties I know I like, but what if I could find wines that match my tastes based on professional wine taster reviews?

## Data Processing
<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/rawdata.png">
</p>
I found a dataset on Kaggle scraped from Wine Enthusiast including ~150,000 wine reviews from 19 wine tasters logging reviews with detailed descriptions, scores, prices, and other metadata. The raw data was fairly clean upon import - not a significant amount of NaNs and no NaN in the description attribute. There were special characters from text written in other languages that had to be cleaned. 

## Data Analysis
<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/ratings.png">
</p>
It seems as though wine reviewers are hesitant to rate a wine a score of 89.

&nbsp;
<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/pricebyscore.png">
</p>
Median wine prices increase drastically in the high 90's, unsurprisingly.

&nbsp;
<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/varieties.png">
</p>
I expected a more flat distribution of varieties being reviewed, but I was surprised to find Pinot Noir and Chardonnay with the most reviews. There were over 750 different wine varietals reviewed in the dataset.

&nbsp;
<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/vintageyears.png">
</p>
Vintage years of the wines reviewed ranged from 1904 to 2018.

&nbsp;
## Topic Modeling
I used an LDA (Latent Dirichlet Allocation) model to categorize the data with a term-frequency bag of words matrix. I also tried NMF (Non-negative Matrix Factorization) with a TF-IDF (inverse document frequency) matrix, but the wines were classified in a strange manner because of the nature of wine reviews and each reviewer potentially sensing a note that others do not (i.e. wood in a Chenin Blanc).

I used english stop words and added additional stop words that weren't helpful in the model. I chose to use the Wordnet lemmatizer because when testing it against snowball and porter stemmers less connotation was lost.

Additional stop words: wine, flavor, aromas, finish, palate, note, nose, drink, fruit, like

I trained the model on an EC2 instance using gensim multicore LDA to speed up training time. 

<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/wordcounthist.png">
</p>

&nbsp;
<p align="center">
  <img src="https://github.com/vanessapolliard/which-wine/blob/master/images/ratingwordcnt.png">
</p>

&nbsp;
### Topics

**[0] Fresh & Fruity** - acidity, fresh, apple, crisp, ripe, blend, tannins, citrus, spice, fruity

**[1] Berry Blend** - cherry, blackberry, cabernet, black, blend, spice, tannins, sweet, acidity, merlot

**[2] Tart Citrus** - white, acidity, peach, lemon, fresh, apple, pear, citrus, offer, body

**[3] Dark & Juicy** - tannins, black, cherry, ripe, rich, acidity, dark, spice, berry, texture

**[4] Dark Berries & Spice** - black, cherry, tannins, acidity, berry, offer, spice, ripe, pepper, fresh

**[5] Full & Smokey** - ripe, rich, tannins, acidity, structure, black, balance, wood, texture, spice

**[6] Warm Spice** - berry, tannins, acidity, plum, spice, cherry, vanilla, feel, herbal, good


&nbsp;
### Example Wines
|  Variety |  Title | Topic Assignments  |
|---|---|---|
|  Riesling |  St. Julian 2013 Reserve Late Harvest Riesling (Lake Michigan Shore) | (2, 0.9494)  |
|  Tempranillo-Merlot |  Tandem 2011 Ars In Vitro Tempranillo-Merlot (Navarra) |  (6, 0.9608) |
| Pinot Gris  | Rainstorm 2013 Pinot Gris (Willamette Valley)  | (0, 0.0628), (2, 0.8923)  |
|  Cabernet Sauvignon |  Louis M. Martini 2012 Cabernet Sauvignon (Alexander Valley) | (4, 0.3363), (6, 0.6158)  |

&nbsp;
### Topic 0 & Topic 6 Top Words
Fresh & Fruity            |  Warm Spice
:-------------------------:|:-------------------------:
![](https://github.com/vanessapolliard/which-wine/blob/master/images/topic0words.png)  |  ![](https://github.com/vanessapolliard/which-wine/blob/master/images/topic6words.png)


&nbsp;
### Model Scores
**log perplexity** = -7.10

**coherence** =  0.35

&nbsp;
### Recommendations
|  Variety |  Title | Topic Assignments  |
|---|---|---|
|  Tempranillo-Merlot | Tandem 2011 Ars In Vitro Tempranillo-Merlot (Navarra)'  | Refosco, Chardonnay, Turbiana, Red Blend, Rhône-style Red Blend, White Blend, Pinot Bianco, Corvina, Cabernet Sauvignon |
|  Pinot Noir | Sweet Cheeks 2012 Vintner's Reserve Wild Child Block Pinot Noir (Willamette Valley)  | Pinot Blanc, Nebbiolo, Sauvignon Blanc, Nebbiolo, Muscato, Rosé, Rosé, Sauvignon Blanc, Cabernet Sauvignon  |

&nbsp;
## Next Steps
Unfortunately because of the size of the dataset I needed to run the model on EC2 using gensim, but gensim does not easily output the typical LDA phi and theta matrices as Sklearn does. When attempting to calculate cosine distances of an NMF model I ran into memory issues on EC2. I plan to use a subset of the data or a memory-optimized EC2 to move forward with generating recommendations from wine to wine (including price and variety as features) and recommendations based on user preferences. 