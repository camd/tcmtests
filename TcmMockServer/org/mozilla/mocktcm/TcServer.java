package org.mozilla.mocktcm;

import org.eclipse.jetty.server.Handler;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.handler.ContextHandlerCollection;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;

public class TcServer {
    public static void main(String[] args) throws Exception {
	Server server = new Server(8080);

	ServletContextHandler context0 = new ServletContextHandler(
		ServletContextHandler.SESSIONS);
	context0.setContextPath("/api/v1");
        context0.addServlet(new ServletHolder(new MockServlet()),
        "/*");

	ContextHandlerCollection contexts = new ContextHandlerCollection();
	contexts.setHandlers(new Handler[] { context0, });

	server.setHandler(contexts);

	server.start();
	server.join();
    }
}