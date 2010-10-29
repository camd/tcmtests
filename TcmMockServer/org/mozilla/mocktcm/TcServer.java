package org.mozilla.mocktcm;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;

public class TcServer {
    public static void main(String[] args) throws Exception {
	Server server = new Server(8080);
	ServletContextHandler root = new ServletContextHandler(server, "/api/v1", ServletContextHandler.SESSIONS);
        root.addServlet(new ServletHolder(new MockServlet()), "/*");
	server.start();
    }
}