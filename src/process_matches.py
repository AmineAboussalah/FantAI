import pandas as pd
import numpy as np


def getRankingFromMatches( matches ):

    homeTeams = matches[ [ 'HOME_TEAM', 'HOME_GOALS', 'AWAY_GOALS' ] ]
    homeTeams = ( homeTeams.rename( columns = { 'HOME_TEAM' : 'TEAM', 'HOME_GOALS' : 'GOALS_FOR', 'AWAY_GOALS' : 'GOALS_AGAINST' } )
        .assign(
            WHERE = 'HOME',
            RESULT = lambda df : np.where( df[ 'GOALS_FOR' ] > df[ 'GOALS_AGAINST' ], 'WIN', np.where( df[ 'GOALS_FOR' ] == df[ 'GOALS_AGAINST' ], 'DRAW', 'LOSS' ) )
        )
        .assign(
            POINTS = lambda df : df[ 'RESULT' ].map( { 'WIN' : 3, 'DRAW' : 1, 'LOSS' : 0 } )
        )
    )
    awayTeams = matches[ [ 'AWAY_TEAM', 'AWAY_GOALS', 'HOME_GOALS' ] ]
    awayTeams = ( awayTeams.rename( columns = { 'AWAY_TEAM' : 'TEAM', 'AWAY_GOALS' : 'GOALS_FOR', 'HOME_GOALS' : 'GOALS_AGAINST' } )
        .assign(
            WHERE = 'AWAY',
            RESULT = lambda df : np.where( df[ 'GOALS_FOR' ] > df[ 'GOALS_AGAINST' ], 'WIN', np.where( df[ 'GOALS_FOR' ] == df[ 'GOALS_AGAINST' ], 'DRAW', 'LOSS' ) )
        )
        .assign(
            POINTS = lambda df : df[ 'RESULT' ].map( { 'WIN' : 3, 'DRAW' : 1, 'LOSS' : 0 } )
        )
    )
    ranking = pd.concat( [ homeTeams, awayTeams ] ).groupby( [ 'TEAM', 'WHERE' ] )[ [ 'POINTS', 'GOALS_FOR', 'GOALS_AGAINST' ] ].sum().unstack()
    ranking.columns = [ '{}_{}'.format( x, y ) for x, y in ranking.columns ]
    ranking = ranking.assign(
        POINTS = lambda df: df[ 'POINTS_HOME' ] + df[ 'POINTS_AWAY' ],
        GOALS_FOR = lambda df: df[ 'GOALS_FOR_HOME' ] + df[ 'GOALS_FOR_AWAY' ],
        GOALS_AGAINST = lambda df: df[ 'GOALS_AGAINST_HOME' ] + df[ 'GOALS_AGAINST_AWAY' ],
    )
    return ( ranking.sort_values( 'POINTS', ascending = False )
        .reset_index()
        .assign( RANKING = range( 1, 21 ) )
    )[ [ 'RANKING', 'TEAM', 'POINTS', 'POINTS_HOME', 'POINTS_AWAY', 'GOALS_FOR', 'GOALS_FOR_HOME', 'GOALS_FOR_AWAY', 'GOALS_AGAINST', 'GOALS_AGAINST_HOME', 'GOALS_AGAINST_AWAY' ] ]


def dumpRankings():
    inputDir = '/home/pierpaolo/Documents/AI/FantAI/data/raw/matches/'
    outputDir = '/home/pierpaolo/Documents/AI/FantAI/data/processed/rankings/'
    fromYear = 2005
    toYear = 2016
    for year in xrange( fromYear, toYear + 1 ):
        matches = pd.read_csv( inputDir + '{}_{}.csv'.format( year, year + 1 ) )
        ranking = getRankingFromMatches( matches )
        ranking.to_csv( outputDir + '{}_{}.csv'.format( year, year + 1 ) )


dumpRankings()




