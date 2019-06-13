jQuery( document ).ready( function( $ ) {
    
    /* Form variables */
    var contribs_form = $('#contribs-form-wrapper form') 
    var contribs_table = $('#contribs-form-wrapper #contribs-table') 
    var contribs_collection = [];
    var utils = new Utils()

    /* Search through MediaWiki API */
    $('#contribs-form-wrapper #btn-search').click(function(e){
        e.preventDefault();
        contribsHandler(contribs_form);
    })
    
    /* Save rows to db */
    $('#contribs-form-wrapper #btn-save').click(function(e){
        e.preventDefault();
        saveContribs(contribs_collection)
    })
    
    /* Clear the table rows */
    $('#contribs-form-wrapper #btn-reset').click(function(e){
        e.preventDefault();
        contribs_table.find('tbody').empty()
    })

    
    /**
     * Handle data related to CU Audit form 
     * @link: https://developers.google.com/apps-script/guides/html/communication
     */
    function contribsHandler(formObject) {
        
        var username = $(formObject).find("input[name=username]").val();
        var wiki = $(formObject).find("input[name=wiki]").val();
        
        if(""!== wiki && ""!= username){
            var mediawiki = new MediaWiki(wiki, username)
            mediawiki
            .getWikiContribs()
                .then(function(contribs){

                    for (var i = 0; i <= contribs.length; i++) {
                        
                        // Add edit to the collection of contribs
                        var edit = contribs[i];
                        contribs_collection.append(edit)
                        var line = contribs_collection.length + 1
                        
                        if (typeof(edit) !== "undefined"){

                            // Append row to Table
                            var html = '<tr>'
                                    html += '<td>' + line + '</td>'
                                    html += '<td>' + edit.timestamp + '</td>'
                                    html += '<td>' + edit.revid + '</td>'
                                    html += '<td>' + edit.user + '</td>'
                                    html += '<td>' + edit.title + '</td>'
                                    html += '<td>' + edit.comment + '</td>'
                                html += '</tr>'
                            
                            $('#contribs-table tbody:last-child')
                            .append(html);

                            console.log(edit)
                        }
                        
                    } 
                    
                })
        }
        
    }

    /**
     * Post result to endpoint. Once its hits the route
     * It will be saved in the DB 
     * */
    function saveContribs(contribs){
        
        var url = utils.baseUrl() + "contribs/save"
        return fetch(url, {
                    method: 'POST',
                    body: JSON.stringify(contribs),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(function(data){
                    return data.json()
                })
                .then(function(json){
                    return json
                })
    }

} );

/**
 * Performs a various range of interactions with
 * the MediaWiki REST API
 * @link: https://www.mediawiki.org/wiki/API:Help
 */
class MediaWiki {
    /**
     * Constructor
     * @param {String} wiki 
     * @param {String} username 
     */
    constructor(wiki, username){
        this.wiki = wiki;
        this.username = username;
    }
    
    /**
     * Get user contributions via API:Contribs
     * @link: https://www.mediawiki.org/wiki/API:Usercontribs
     */
    getWikiContribs() {
        var limit = 50;
        // Get the base url
        var baseUrl = utils.getBaseUrl();
        var query = "uclimit=" + limit +
        "&format=json&list=usercontribs&ucuser=" + this.username;
        url = baseUrl + "query/" + query + "/" + this.wiki
        
        return fetch(url)
                .then(function(data){
                    return data.json()
                })
                .then(function(json){
                    return json.query.usercontribs
                })      
    }
}

class Utils{
    /**
     * Get Homeurl
     */
    getBaseUrl() {
        // use home url link as baseurl, remove protocol
        var baseUrl = document.getElementById( 'baseurl' ).getAttribute( 'href' ).replace( /^https?:\/\//,'' );
        // add actual protocol to fix Flask bug with protocol inconsistency
        //baseUrl = location.protocol + '//' + baseUrl
        return baseUrl;
    }
}