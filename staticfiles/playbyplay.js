const fetchData = async () => {
  const gameID = document.querySelector('#gameID').textContent
  const urlGI = encodeURIComponent(gameID)
  const url = `https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLBoxScore?gameID=${urlGI}&playByPlay=true&twoPointConversions=2&passYards=.04&passAttempts=0&passTD=4&passCompletions=0&passInterceptions=-2&pointsPerReception=.5&carries=.2&rushYards=.1&rushTD=6&fumbles=-2&receivingYards=.1&receivingTD=6&targets=0&defTD=6&fgMade=3&fgMissed=-3&xpMade=1&xpMissed=-1`;
  const options = {
    method: 'GET',
    headers: {
      'x-rapidapi-key': '57106580edmshaf54e7fc6006b35p145d26jsn76b265a565c0',
      'x-rapidapi-host': 'tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com'
    }
  };
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    console.log("GAME ID: ", gameID);
    console.log("data on js: ",data);
	  //    const dandd = data.body.allPlayByPlay[0].downAndDistance;
    // Extract specific data
    const allPlayByPlay = data.body.allPlayByPlay;
    document.getElementById('nowplay').textContent = `${allPlayByPlay[0].play}`;
    document.getElementById('homename').textContent = `${data.body.home}`;
    document.getElementById('awayname').textContent = `${data.body.away}`;
    document.getElementById('currentperiod').textContent = `${data.body.currentPeriod}`;
    document.getElementById('gameclock').textContent = `${data.body.gameClock}`;
    document.getElementById('homepoints').textContent = `${data.body.homePts}`;
    document.getElementById('awaypoints').textContent = `${data.body.awayPts}`;
  //  document.getElementById('dandd').textContent = `${dandd}`;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};
// Fetch data every 5 seconds
setInterval(fetchData, 15000);

// Initial fetch when the page loads
fetchData();
