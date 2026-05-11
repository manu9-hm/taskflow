import { format } from "date-fns";

const PRIORITY_STYLES = {
  low: "bg-gray-700 text-gray-300",
  medium: "bg-blue-900/50 text-blue-300",
  high: "bg-orange-900/50 text-orange-300",
  urgent: "bg-red-900/50 text-red-300",
};

const STATUS_STYLES = {
  todo: "bg-gray-700 text-gray-300",
  in_progress: "bg-yellow-900/50 text-yellow-300",
  done: "bg-green-900/50 text-green-300",
};

const STATUS_LABEL = { todo: "To Do", in_progress: "In Progress", done: "Done" };

export default function TaskCard({ task, onEdit, onDelete }) {
  const tags = task.tags ? task.tags.split(",").map((t) => t.trim()).filter(Boolean) : [];

  return (
    <div className="card flex flex-col gap-3 hover:border-gray-700 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-white text-sm leading-snug flex-1">{task.title}</h3>
        <div className="flex gap-1 shrink-0">
          <button
            onClick={() => onEdit(task)}
            className="text-gray-400 hover:text-white p-1 rounded transition-colors"
            title="Edit"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="text-gray-400 hover:text-red-400 p-1 rounded transition-colors"
            title="Delete"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Description */}
      {task.description && (
        <p className="text-gray-400 text-xs leading-relaxed line-clamp-2">{task.description}</p>
      )}

      {/* Badges */}
      <div className="flex flex-wrap gap-1.5">
        <span className={`badge ${STATUS_STYLES[task.status]}`}>
          {STATUS_LABEL[task.status]}
        </span>
        <span className={`badge ${PRIORITY_STYLES[task.priority]}`}>
          {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
        </span>
        {tags.map((tag) => (
          <span key={tag} className="badge bg-gray-800 text-gray-300">#{tag}</span>
        ))}
      </div>

      {/* Footer */}
      {task.due_date && (
        <p className="text-xs text-gray-500">
          Due {format(new Date(task.due_date), "MMM d, yyyy")}
        </p>
      )}
    </div>
  );
}
