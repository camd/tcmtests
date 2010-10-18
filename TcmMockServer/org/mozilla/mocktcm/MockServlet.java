package org.mozilla.mocktcm;

import java.io.BufferedReader;
import java.io.IOException;
import java.net.URLDecoder;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.Gson;

public class MockServlet extends HttpServlet {

    Gson gson = new Gson();
    Step[] steps;
    int currentStep = 0;

    public MockServlet() {
    }

    protected void doGet(HttpServletRequest request,
            HttpServletResponse response) throws ServletException, IOException {
        
        // print out the request, so we can debug this on the server side.
        String reqStr = request.toString();
        reqStr = reqStr.substring(0, reqStr.indexOf("@"));
        System.out.println(reqStr);
        try {
            if (request.getPathInfo() != null
                    && request.getPathInfo().indexOf("/mockdata") > -1) {
                String stepJson = getPostData(request);

                steps = gson.fromJson(stepJson, Step[].class);
                currentStep = 0;
            }
            // Return the next expected value for the current steps
            else if (steps != null && currentStep < steps.length) {
                response.setContentType("text/xml");               
                response.setStatus(steps[currentStep].status);
                /*
                 * The expected response is sent as JSON within a field of JSON.  So 
                 * I had to encode the embedded JSON.  However, when I return it, I want 
                 * to send it as decoded JSON, so it looks normal and is parse-able.
                 * Therefore, I must decode it here.
                 */
                String responseStr = URLDecoder.decode(steps[currentStep].response, "UTF-8");
                response.getWriter().println(responseStr);
                currentStep++;
            }
            // request not handled, just return error
            else {
                System.out.println("Wasn't handled.  Returning NOT IMPLEMENTED");
                response.setContentType("text/xml");
                response.setStatus(HttpServletResponse.SC_NOT_IMPLEMENTED);
            }
        } catch (com.google.gson.JsonParseException ex) {
            System.out.println("Well, that didn't work...");
            ex.printStackTrace();
        }

    }

    
    
    /*
     * These are all handled exactly the same as any request in this mock object. 
     */
    
    
    
    public void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }
    
    protected void doDelete(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }

    protected void doPut(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }

    /*
     * Helper function
     * Just read the string content of the post data into a string
     */
    protected String getPostData(HttpServletRequest request)
            throws ServletException, IOException {
        BufferedReader reader = new BufferedReader(request.getReader());
        StringBuffer strBuf = new StringBuffer();
        char[] c = new char[request.getContentLength()];
        reader.read(c);
        strBuf.append(c);
        String body = strBuf.toString();
        return body;
    }

}

/**
 * This is used as the java representation of the JSON that comes in to
 * represent the responses for each step of the next test Scenario
 * 
 * @author camerondawson
 * 
 */
class Step {
    int status;
    String response;

    Step() {
    }
}
