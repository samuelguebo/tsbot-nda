jQuery( document ).ready( function( $ ) {
    
    $('#contribs-form-wrapper form').submit(function(e) {
        e.preventDefault(); // disable default behavior
        contribsFormHandler(this);
    })

} );

/**
 * Handle data related to CU Audit form 
 * @link: https://developers.google.com/apps-script/guides/html/communication
 */
function contribsFormHandler(formObject) {
    var rows = [];
    var username = formObject.username.toString();
    var wiki = 'https://' + formObject.wiki.toString();
    var contribs = getWikiContribs(wiki, username);
    
    for (var i = 0; i < contribs.length; i++) {
      var edit = contribs[i];
      rows[i] = {
        'timestamp': edit.timestamp,
        'revid': edit.revid,
        'user': edit.user,
        'title': edit.title,
        'comment': edit.comment
      };
    } 
}

/**
 * Get user contributions via API:Contribs
 * @link: https://www.mediawiki.org/wiki/API:Usercontribs
 */
function getWikiContribs(wiki, username) {
    var limit = 50;
    // Get the base url
    baseUrl = getBaseUrl();
    var query = "uclimit=" + limit +
      "&format=json&list=usercontribs&ucuser=" + username;
    url = baseUrl + "/query/" + query + "/" + wiki
    
    
    return fetch(url)
            .then(function(data){
                var contribs = JSON.parse(data).query.usercontribs
                console.log(contribs)
                return contribs;
            })      
}

/**
 * Get Homeurl
 */
function getBaseUrl() {
	// use home url link as baseurl, remove protocol
	var baseUrl = document.getElementById( 'baseurl' ).getAttribute( 'href' ).replace( /^https?:\/\//,'' );
	// add actual protocol to fix Flask bug with protocol inconsistency
	baseUrl = location.protocol + '//' + baseUrl
	return baseUrl;
}