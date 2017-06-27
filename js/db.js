var db = new loki('sandbox.db');

// Add a collection to the database
var votes = db.addCollection('votes');
var scrutins = db.addCollection('scrutins');
$.ajax({
  //url: 'https://cdn.rawgit.com/maxkfranz/3d4d3c8eb808bd95bae7/raw', // wine-and-cheese.json
  url: 'votes.json',
  type: 'GET',
  dataType: 'json'
}).done(function(data) {
  data.forEach(function (o) {
     votes.insert(o);
  });
  test();
});

// Add some documents to the collection

// Find and update an existing document
function test() {
  var tyrfing = votes.findOne({ uid:'VTANR5L14V1'});
  console.log(tyrfing);
  console.log(votes);
}


var substringMatcher = function(strs) {
  return function findMatches(q, cb) {
    var matches, substringRegex;

    // an array that will be populated with substring matches
    matches = [];

    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');

    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
        matches.push(str);
      }
    });

    cb(matches);
  };
};

$('#the-basics .typeahead').typeahead({
  hint: true,
  highlight: true,
  minLength: 1
},
{
  name: 'scrutins',
  source: substringMatcher(votes)
});
