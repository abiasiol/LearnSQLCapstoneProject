# OlympicsAthletesSQL

Analysis of the SportsStats dataset using SQL, Pandas, Plotly in a Jupyter Notebook.
Look at the final result with interactive maps and plots here: https://andrea-olympics-sql.herokuapp.com/

<br>

## Goal of the analysis
The analysis relies on the SportsStats dataset to study country-wide patterns in terms of medal earning.

The goal is to understand which countries are currently performing better and which countries are on the rise.

Additional information provided include an analysis on whether different NOCs rely on single high-talent individuals competing in more editions/events, and which parameters correlate better with winning medals.

# Question 1
## Which countries are currently the most successful (in terms of number of medals) and which ones are on the rise?

- It can be helpful to know if similarly-sized countries are faring better or worse
- It can also be helpful to see which countries are consistently performing well (maybe they established a good funding/coaching system)


# Question 2
## Which countries relies mostly on single-athletes performance to obtain their medals?

Some countries performance will be reliant on single individuals. This is not too promising for their future, as when the athlete retires the country performance will likely worsen.


# Question 3
## Is there any connection between the height and the expected performance?

- Sometimes young athletes are selected based on their technical skills, and not their physical potential. If a relationship is found between height and performance, maybe the recruiting process could be different and encourage physical-based down selection.
- Height may be relevant in more recent editions but not in earlier ones. Is the importance changing in time?
- The analysis should be differentiated based on sex

# Executive summary
- United States and France are currently some of the most successful countries, quickly increasing their dominance. Russia and China hold on to a large number of medals, but their record prospects are not looking well. Reasons may lie in the doping scandal for Russia and in the recent edition hosting for China, which temporarily impacted China's record (more medals earned in 2008, and a decreasing record in the next editions)
- Comparisons with similar-sized countries can only be carried out with average or small size countries. In fact, the highest-ranked countries like USA, Russia, and China are not really comparable among them in size while they are in terms of performance.
- Largest countries are the ones relies on competing with one athlete in multiple events
- Athlete per event metric is likely not indicative of the future prospects of a country Olympics performance
- Height is strongly positively correlated to the performance (in terms of number of medals earned)
- Data before WWII is unreliable (missing)
- Both M/F are taller in recent editions, with M being on average 11cm taller than F
- Summer athletes are on average consistently taller and heavier than Winter athletes
