import urllib2
from bs4 import BeautifulSoup
import pandas as pd

for year in range( 2005, 2017 ):
    url = 'https://www.tuttomercatoweb.com/calendario_classifica/serie_a/{}-{}'.format( year, year + 1)
    page = urllib2.urlopen( url )
    soup = BeautifulSoup( page )
    toConcat = []
    for table in soup.findAll( 'table' ):
        lines = table.findAll( 'td' )
        firstLine = next( ( i for i, line in enumerate( lines ) if line.find( text = True ) is not None and line.find( text = True ).strip()[:8] == 'Giornata' ), None )
        if firstLine is None:
            continue
        days, dates, homeTeams, awayTeams, homeGoals, awayGoals = [], [], [], [], [], []
        day = int( lines[ firstLine ].find( text = True )[ 12: ] )
        dateFirst = pd.to_datetime( lines[ firstLine + 1 ].find( text = True ), format = '%d/%m/%Y' )
        dateSecond = pd.to_datetime( lines[ firstLine + 2 ].find( text = True ), format = '%d/%m/%Y' )
        for i in xrange( firstLine + 3, firstLine + 32, 3 ):
            firstTeam, secondTeam = lines[ i ].find( text = True ).strip().split( '-' )
            homeGoals1, awayGoals1 = lines[ i + 1 ].find( text = True ).strip().split( '-' )
            awayGoals2, homeGoals2 = lines[ i + 2 ].find( text = True ).strip().split( '-' )
            days += [ day, day + 19 ]
            dates += [ dateFirst, dateSecond ]
            homeTeams += [ firstTeam, secondTeam ]
            awayTeams += [ secondTeam, firstTeam ]
            homeGoals += [ homeGoals1, homeGoals2 ]
            awayGoals += [ awayGoals1, awayGoals2 ]
        dfDay = pd.DataFrame( { 'DAY' : days, 'DATE' : dates, 'HOME_TEAM' : homeTeams, 'AWAY_TEAM' : awayTeams, 'HOME_GOALS' : homeGoals, 'AWAY_GOALS' : awayGoals } )
        dfDay = dfDay[ [ 'DAY', 'DATE', 'HOME_TEAM', 'AWAY_TEAM', 'HOME_GOALS', 'AWAY_GOALS' ] ]
        dfDay[ 'HOME_GOALS' ] = dfDay[ 'HOME_GOALS' ].astype( int )
        dfDay[ 'AWAY_GOALS' ] = dfDay[ 'AWAY_GOALS' ].astype( int )
        toConcat.append( dfDay )
    df = pd.concat( toConcat ).drop_duplicates().sort_values( 'DAY' ).reset_index( drop = True )
    df.to_csv( '/home/pierpaolo/Documents/AI/FantAI/data/raw/results_{}_{}.csv'.format( year, year + 1 ) )
    print df.head()
