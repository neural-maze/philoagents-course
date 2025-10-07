package spring.ai.philoagents.workflow;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

import org.bsc.langgraph4j.serializer.StateSerializer;
import org.bsc.langgraph4j.state.AgentState;
import org.springframework.ai.support.ToolCallbacks;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.ToolCallbackProvider;

public abstract class AgentExecutorBuilder<B extends AgentExecutorBuilder<B, S>, S extends AgentState> {
        StateSerializer<S> stateSerializer;

    String systemMessage;
    boolean streaming = false;

    final List<ToolCallback> tools = new ArrayList<>();
    

    @SuppressWarnings("unchecked")
    protected B result() {
        return (B)this;
    }
    /**
     * Sets the state serializer for the graph builder.
     *
     * @param stateSerializer the state serializer to set
     * @return the current instance of GraphBuilder for method chaining
     */
    public B stateSerializer(StateSerializer<S> stateSerializer) {
        this.stateSerializer = stateSerializer;
        return result();
    }

    public B defaultSystem(String systemMessage) {
        this.systemMessage = systemMessage;
        return result();
    }

    public B tool(ToolCallback tool) {
        this.tools.add(Objects.requireNonNull(tool, "tool cannot be null!"));
        return result();
    }

    public B tools(List<ToolCallback> tools) {
        this.tools.addAll(Objects.requireNonNull(tools, "tools cannot be null!"));
        return result();
    }

    public B tools(ToolCallbackProvider toolCallbackProvider) {
        Objects.requireNonNull(toolCallbackProvider, "toolCallbackProvider cannot be null!");
        var toolCallbacks = toolCallbackProvider.getToolCallbacks();
        if (toolCallbacks.length == 0) {
            throw new IllegalArgumentException("toolCallbackProvider.getToolCallbacks() cannot be empty!");
        }
        this.tools.addAll(List.of(toolCallbacks));
        return result();
    }

    public B toolsFromObject(Object objectWithTools) {
        var tools = ToolCallbacks.from(Objects.requireNonNull(objectWithTools, "objectWithTools cannot be null"));
        this.tools.addAll(List.of(tools));
        return result();
    }
}
