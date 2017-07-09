import pandas as pd
import numpy as np


def preprocessMatches( matches ):
    '''
    Function to preprocess matches and transform them from an horizontal format (e.g. Inter - Juventus 2 - 1 ), to a
    vertical format, with only one team per row. This format is easier to manipulate to compute rankings.

    Params
    ------
    matches: pd.DataFrame
        Matches' results.

    Returns
    -------
    pd.DataFrame:
        Matches' results in vertical format.
    '''
    homeTeams = matches[ [ 'DAY', 'HOME_TEAM', 'HOME_GOALS', 'AWAY_GOALS' ] ]
    homeTeams = ( homeTeams.rename( columns = { 'HOME_TEAM' : 'TEAM', 'HOME_GOALS' : 'GOALS_FOR', 'AWAY_GOALS' : 'GOALS_AGAINST' } )
        .assign(
            WHERE = 'HOME',
            RESULT = lambda df : np.where( df[ 'GOALS_FOR' ] > df[ 'GOALS_AGAINST' ], 'WIN', np.where( df[ 'GOALS_FOR' ] == df[ 'GOALS_AGAINST' ], 'DRAW', 'LOSS' ) )
        )
        .assign(
            POINTS = lambda df : df[ 'RESULT' ].map( { 'WIN' : 3, 'DRAW' : 1, 'LOSS' : 0 } )
        )
    )
    awayTeams = matches[ [ 'DAY', 'AWAY_TEAM', 'AWAY_GOALS', 'HOME_GOALS' ] ]
    awayTeams = ( awayTeams.rename( columns = { 'AWAY_TEAM' : 'TEAM', 'AWAY_GOALS' : 'GOALS_FOR', 'HOME_GOALS' : 'GOALS_AGAINST' } )
        .assign(
            WHERE = 'AWAY',
            RESULT = lambda df : np.where( df[ 'GOALS_FOR' ] > df[ 'GOALS_AGAINST' ], 'WIN', np.where( df[ 'GOALS_FOR' ] == df[ 'GOALS_AGAINST' ], 'DRAW', 'LOSS' ) )
        )
        .assign(
            POINTS = lambda df : df[ 'RESULT' ].map( { 'WIN' : 3, 'DRAW' : 1, 'LOSS' : 0 } )
        )
    )
    return pd.concat( [ homeTeams, awayTeams ] )

def getRankingFromMatches( verticalMatches, day = 38 ):
    '''
    Aggregate matches to obtain the ranking at a given day of the season.

    Params
    ------
    verticalMatches: pd.DataFrame
        Matches' results, in vertical format.

    Returns
    -------
    pd.DataFrame:
        Final ranking.
    '''
    verticalMatches = verticalMatches[ verticalMatches[ 'DAY' ] <= day ]
    ranking = ( verticalMatches.groupby( [ 'TEAM', 'WHERE' ] )
        .agg( {
            'RESULT' : [
                ( 'GAMES', 'count' ),
                ( 'WINS' , lambda g : ( g == 'WIN' ).sum() ),
                ( 'DRAWS' , lambda g : ( g == 'DRAW' ).sum() ),
                ( 'LOSSES' , lambda g : ( g == 'LOSS' ).sum() ),
            ],
            'POINTS' : 'sum',
            'GOALS_FOR' : 'sum',
            'GOALS_AGAINST' : 'sum',
        } )
        .unstack()
    )
    ranking.columns = [ '_'.join( colNames ) for colNames in ranking.columns ]
    ranking = ( ranking.rename(
            columns = { colName : colName.replace( 'RESULT_', '' ).replace( 'sum_', '' ) for colName in ranking.columns }
        )
        .fillna( 0.0 )
        .assign(
            GAMES = lambda df: df[ 'GAMES_HOME' ] + df[ 'GAMES_AWAY' ],
            WINS = lambda df: df[ 'WINS_HOME' ] + df[ 'WINS_AWAY' ],
            DRAWS = lambda df: df[ 'DRAWS_HOME' ] + df[ 'DRAWS_AWAY' ],
            LOSSES = lambda df: df[ 'LOSSES_HOME' ] + df[ 'LOSSES_AWAY' ],
            POINTS = lambda df: df[ 'POINTS_HOME' ] + df[ 'POINTS_AWAY' ],
            GOALS_FOR = lambda df: df[ 'GOALS_FOR_HOME' ] + df[ 'GOALS_FOR_AWAY' ],
            GOALS_AGAINST = lambda df: df[ 'GOALS_AGAINST_HOME' ] + df[ 'GOALS_AGAINST_AWAY' ],
        )
    )
    return ( ranking.sort_values( 'POINTS', ascending = False )
        .reset_index()
        .assign( RANKING = range( 1, 21 ) )
    )[ [ 'RANKING', 'TEAM',
         'POINTS', 'GAMES', 'WINS', 'DRAWS', 'LOSSES', 'GOALS_FOR', 'GOALS_AGAINST',
         'POINTS_HOME', 'GAMES_HOME', 'WINS_HOME', 'DRAWS_HOME', 'LOSSES_HOME', 'GOALS_FOR_HOME', 'GOALS_AGAINST_HOME',
         'POINTS_AWAY', 'GAMES_AWAY', 'WINS_AWAY', 'DRAWS_AWAY', 'LOSSES_AWAY', 'GOALS_FOR_AWAY', 'GOALS_AGAINST_AWAY' ] ]


def getRankingEvolutionFromMatches( verticalMatches ):
    '''
    Get the ranking evolution day by day.

    Params
    ------
    verticalMatches: pd.DataFrame
        Matches' results, in vertical format.

    Returns
    -------
    pd.DataFrame:
        Ranking evolution, day by day.
    '''
    return pd.concat( getRankingFromMatches( verticalMatches, day ).assign( DAY = day ) for day in xrange( 1, 39 ) )

def dumpRankings():
    inputDir = '/home/pierpaolo/Documents/AI/FantAI/data/raw/matches/'
    outputDir = '/home/pierpaolo/Documents/AI/FantAI/data/processed/rankings/'
    fromYear = 2005
    toYear = 2016
    for year in xrange( fromYear, toYear + 1 ):
        matches = pd.read_csv( inputDir + '{}_{}.csv'.format( year, year + 1 ) )
        verticalMatches = preprocessMatches( matches )
        ranking = getRankingFromMatches( verticalMatches )
        ranking.to_csv( outputDir + '{}_{}.csv'.format( year, year + 1 ) )

def dumpRankingEvolutions():
    inputDir = '/home/pierpaolo/Documents/AI/FantAI/data/raw/matches/'
    outputDir = '/home/pierpaolo/Documents/AI/FantAI/data/processed/ranking_evolutions/'
    fromYear = 2005
    toYear = 2016
    for year in xrange( fromYear, toYear + 1 ):
        matches = pd.read_csv( inputDir + '{}_{}.csv'.format( year, year + 1 ) )
        verticalMatches = preprocessMatches( matches )
        ranking = getRankingEvolutionFromMatches( verticalMatches )
        ranking.to_csv( outputDir + '{}_{}.csv'.format( year, year + 1 ) )

dumpRankingEvolutions()




