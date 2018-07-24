var url = "https://api.nytimes.com/svc/topstories/v2/politics.json";
url += '?' + $.param({
  'api-key': "d10b328c51b3493ba039288cc0d88b76"
});
$.ajax({
  url: url,
  method: 'GET',
}).done(function(result) {
  console.log(result);
}).fail(function(err) {
  throw err;
});